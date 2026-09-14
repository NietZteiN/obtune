#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    std::vector<long> new_lst;
    long i = lst.size() - 1;
    for (int j = 0; j < lst.size(); j++) {
        if (i % 2 == 0) {
            new_lst.push_back(-lst[i]);
        } else {
            new_lst.push_back(lst[i]);
        }
        i--;
    }
    return new_lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)7, (long)-1, (long)-3}))) == (std::vector<long>({(long)-3, (long)1, (long)7, (long)-1})));
}
