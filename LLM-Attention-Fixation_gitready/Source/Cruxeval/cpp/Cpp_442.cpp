#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    std::vector<long> res;
    for (int i = 0; i < lst.size(); i++) {
        if (lst[i] % 2 == 0) {
            res.push_back(lst[i]);
        }
    }
    
    return lst;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4}))) == (std::vector<long>({(long)1, (long)2, (long)3, (long)4})));
}
