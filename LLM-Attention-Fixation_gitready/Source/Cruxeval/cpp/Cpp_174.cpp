#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    if (lst.size() > 1) {
        size_t start = 1;
        size_t end = std::min(lst.size(), (size_t)4);
        std::reverse(lst.begin() + start, lst.begin() + end);
    }
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3}))) == (std::vector<long>({(long)1, (long)3, (long)2})));
}
