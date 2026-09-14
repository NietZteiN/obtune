#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> lst) {
    int i = 0;
    std::vector<long> new_list;
    while(i < lst.size()) {
        if(std::find(lst.begin() + i + 1, lst.end(), lst[i]) != lst.end()) {
            new_list.push_back(lst[i]);
            if(new_list.size() == 3) {
                return new_list;
            }
        }
        i++;
    }
    return new_list;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)2, (long)1, (long)2, (long)6, (long)2, (long)6, (long)3, (long)0}))) == (std::vector<long>({(long)0, (long)2, (long)2})));
}
