#include <cstdio>
#include <chrono>
#include <opencv2/opencv.hpp>
#include <Eigen/Dense>

using namespace std;
using namespace cv;
using namespace Eigen;

int main(){
    int N = 0;
    int idx = 1;
    
    printf("Quantas imagens? ");
    scanf("%d", &N);

    char path[100];
    while (idx <= N){
        if (idx > 1) printf("\n");

        // Leitura da imagem
        sprintf(path, "imgs/original/in_%d.png", idx);
        Mat img = imread(path, IMREAD_COLOR);
        if (img.empty()){
            printf("Imagem nao encontrada.");
            return -1;
        }

        int n = img.rows;
        int m = img.cols;

        printf("Imagem %d carregada (%d x %d).\n", idx, n, m);

        Mat A;
        img.convertTo(A, CV_32F, 1.0/255.0);

        Mat M(n, m, CV_8U);
        randu(M, 0, 256);
        threshold(M, M, 127, 1, THRESH_BINARY); // 50% esparsa

        // Geracao da imagem esparsa
        for (int i=0; i<n; i++)
            for (int j=0; j<m; j++)
                if (M.at<uchar>(i, j) == 0)
                    A.at<Vec3f>(i, j) = Vec3f(0, 0, 0);

        // Separacao dos canais
        vector<Mat> C;
        split(A, C);

        int k = 50;
        int kmax = 20;

        chrono::duration<double> s_total = chrono::duration<double>::zero();
        char cores[3] = {'R','G','B'};

        for (int c=0; c<3; c++){
            // ALS
            auto inicio = chrono::high_resolution_clock::now();

            MatrixXf U = MatrixXf::Random(n, k);
            MatrixXf V = MatrixXf::Random(m, k);

            printf("Reconstruindo o canal %c...", cores[c]);
            fflush(stdout);

            for (int l=0; l<kmax; l++){
                // Atualiza U
                for (int i=0; i<n; i++){
                    vector<int> I;
                    for (int j=0; j<m; j++)
                        if (M.at<uchar>(i, j) == 1) I.push_back(j);
                    
                    if (I.empty()) continue;

                    MatrixXf X(I.size(), k);
                    VectorXf y(I.size());

                    for (int j=0; j<I.size(); j++){
                        X.row(j) = V.row(I[j]);
                        y(j) = C[c].at<float>(i, I[j]);
                    }

                    VectorXf u_i = (X.transpose() * X).ldlt().solve(X.transpose() * y);
                    U.row(i) = u_i;
                }

                // Atualiza V
                for (int j=0; j<m; j++){
                    vector<int> J;
                    for (int i=0; i<n; i++)
                        if (M.at<uchar>(i, j) == 1) J.push_back(i);
                    
                    if (J.empty()) continue;

                    MatrixXf X(J.size(), k);
                    VectorXf y(J.size());

                    for (int i=0; i<J.size(); i++){
                        X.row(i) = U.row(J[i]);
                        y(i) = C[c].at<float>(J[i], j);
                    }

                    VectorXf v_i = (X.transpose() * X).ldlt().solve(X.transpose() * y);
                    V.row(j) = v_i;
                }
            }

            // Reconstroi o canal
            MatrixXf C_rec = U * V.transpose();
            for (int i=0; i<n; i++)
                for (int j=0; j<m; j++)
                    C[c].at<float>(i, j) = C_rec(i, j);
            
            auto final = chrono::high_resolution_clock::now();
            chrono::duration<double> s = final - inicio;
            s_total += s;
            
            printf(" [ok] <%.2f segundos>\n", s.count());
        }

        A.convertTo(A, CV_8U, 255.0);

        Mat imgRec;
        merge(C, imgRec);
        imgRec.convertTo(imgRec, CV_8U, 255.0);

        
        /*// Mostra as imagens
        imshow("Imagem original", img);
        imshow("Imagem 50%% esparsa", A);
        imshow("Imagem Reconstruida (ALS & MMQ)", imgRec);*/

        // Salva as imagens
        sprintf(path, "imgs/esparsa/out_%d_50perc.png", idx);
        imwrite(path, A);

        sprintf(path, "imgs/reconstruida/out_%d_ALS.png", idx);
        imwrite(path, imgRec);

        printf("Imagem %d concluida! Tempo total de execucao: %.2f segundos.\n", idx++, s_total.count());

        /*printf("Pressione ESC para sair.\n");
        while (true) if (waitKey(0) == 27) break;*/
    }

    return 0;
}