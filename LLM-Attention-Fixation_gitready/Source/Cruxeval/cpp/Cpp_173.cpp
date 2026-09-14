#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> list_x) {
    int item_count = list_x.size();
    std::vector<long> new_list;
    for (int i = 0; i < item_count; i++) {
        new_list.push_back(list_x.back());
        list_x.pop_back();
    }
    return new_list;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)5, (long)8, (long)6, (long)8, (long)4}))) == (std::vector<long>({(long)4, (long)8, (long)6, (long)8, (long)5})));
}
