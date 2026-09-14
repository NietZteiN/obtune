#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> num) {
    num.push_back(num.back());
    return num;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-70, (long)20, (long)9, (long)1}))) == (std::vector<long>({(long)-70, (long)20, (long)9, (long)1, (long)1})));
}
