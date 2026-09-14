#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    for(int i = 0; i < nums.size() - 1; i++){
        std::reverse(nums.begin(), nums.end());
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)-9, (long)7, (long)2, (long)6, (long)-3, (long)3}))) == (std::vector<long>({(long)1, (long)-9, (long)7, (long)2, (long)6, (long)-3, (long)3})));
}
