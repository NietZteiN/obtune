#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    std::vector<long> l;
    for (long i : nums) {
        if (std::find(l.begin(), l.end(), i) == l.end()) {
            l.push_back(i);
        }
    }
    return l;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)1, (long)9, (long)0, (long)2, (long)0, (long)8}))) == (std::vector<long>({(long)3, (long)1, (long)9, (long)0, (long)2, (long)8})));
}
