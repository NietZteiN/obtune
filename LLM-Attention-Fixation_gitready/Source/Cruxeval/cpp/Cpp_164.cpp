#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    std::sort(lst.begin(), lst.end());
    std::vector<long> result(lst.begin(), lst.begin() + 3);
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)8, (long)1, (long)3, (long)0}))) == (std::vector<long>({(long)0, (long)1, (long)3})));
}
