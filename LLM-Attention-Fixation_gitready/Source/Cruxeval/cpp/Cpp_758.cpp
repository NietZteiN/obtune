#include<assert.h>
#include<bits/stdc++.h>
bool f(std::vector<long> nums) {
    std::vector<long> reversed_nums = nums;
    std::reverse(reversed_nums.begin(), reversed_nums.end());
    
    if (reversed_nums == nums) {
        return true;
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)3, (long)6, (long)2}))) == (false));
}
