#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> arr) {
    std::reverse(arr.begin(), arr.end());
    return arr;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)0, (long)1, (long)9999, (long)3, (long)-5}))) == (std::vector<long>({(long)-5, (long)3, (long)9999, (long)1, (long)0, (long)2})));
}
