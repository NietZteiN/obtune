#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, long n) {
    return std::vector<long>(array.begin() + n, array.end());
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)0, (long)1, (long)2, (long)2, (long)2, (long)2})), (4)) == (std::vector<long>({(long)2, (long)2, (long)2})));
}
