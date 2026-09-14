#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> L) {
    int N = L.size();
    for (int k = 1; k <= N/2; ++k) {
        int i = k - 1;
        int j = N - k;
        while (i < j) {
            std::swap(L[i], L[j]);
            i++;
            j--;
        }
    }
    return L;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)16, (long)14, (long)12, (long)7, (long)9, (long)11}))) == (std::vector<long>({(long)11, (long)14, (long)7, (long)12, (long)9, (long)16})));
}
