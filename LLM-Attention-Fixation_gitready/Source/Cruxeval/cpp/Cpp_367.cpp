#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long rmvalue) {
    std::vector<long> res = nums;
    while(std::find(res.begin(), res.end(), rmvalue) != res.end()) {
        auto it = std::find(res.begin(), res.end(), rmvalue);
        res.erase(it);
        if (*it != rmvalue) {
            res.push_back(*it);
        }
    }
    return res;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)2, (long)1, (long)1, (long)4, (long)1})), (5)) == (std::vector<long>({(long)6, (long)2, (long)1, (long)1, (long)4, (long)1})));
}
