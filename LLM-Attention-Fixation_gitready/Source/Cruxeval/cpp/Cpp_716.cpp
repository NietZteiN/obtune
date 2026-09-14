#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size();
    while(nums.size() > (count / 2)) {
        nums.clear();
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)1, (long)2, (long)3, (long)1, (long)6, (long)3, (long)8}))) == (std::vector<long>()));
}
