#include<assert.h>
#include<bits/stdc++.h>
long f(long n, long m, long num) {
    std::vector<long> x_list;
    for (long i = n; i <= m; i++) {
        x_list.push_back(i);
    }
    
    long j = 0;
    while (true) {
        j = (j + num) % x_list.size();
        if (x_list[j] % 2 == 0) {
            return x_list[j];
        }
    }
}
int main() {
    auto candidate = f;
    assert(candidate((46), (48), (21)) == (46));
}
