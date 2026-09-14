#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    std::reverse(lst.begin(), lst.end());
    lst.pop_back();
    std::reverse(lst.begin(), lst.end());
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)7, (long)8, (long)2, (long)8}))) == (std::vector<long>({(long)8, (long)2, (long)8})));
}
