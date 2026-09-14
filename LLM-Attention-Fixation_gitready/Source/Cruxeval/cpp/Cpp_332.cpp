#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    if (count == 0) {
        int value = nums.back();
        nums = std::vector<long>(value, 0);
    } else if (count % 2 == 0) {
        nums.clear();
    } else {
        nums.erase(nums.begin(), nums.begin() + count/2);
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-6, (long)-2, (long)1, (long)-3, (long)0, (long)1}))) == (std::vector<long>()));
}
