#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> base_list, std::vector<long> nums) {
    base_list.insert(base_list.end(), nums.begin(), nums.end());
    std::vector<long> res = base_list;
    for (int i = -nums.size(); i < 0; i++) {
        res.push_back(res[i + res.size()]);
    }
    return res;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)9, (long)7, (long)5, (long)3, (long)1})), (std::vector<long>({(long)2, (long)4, (long)6, (long)8, (long)0}))) == (std::vector<long>({(long)9, (long)7, (long)5, (long)3, (long)1, (long)2, (long)4, (long)6, (long)8, (long)0, (long)2, (long)6, (long)0, (long)6, (long)6})));
}
