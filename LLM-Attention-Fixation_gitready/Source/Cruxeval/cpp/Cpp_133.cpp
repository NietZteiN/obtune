#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, std::vector<long> elements) {
    std::vector<long> result;
    for (int i = 0; i < elements.size(); i++) {
        result.push_back(nums.back());
        nums.pop_back();
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)7, (long)1, (long)2, (long)6, (long)0, (long)2})), (std::vector<long>({(long)9, (long)0, (long)3}))) == (std::vector<long>({(long)7, (long)1, (long)2})));
}
