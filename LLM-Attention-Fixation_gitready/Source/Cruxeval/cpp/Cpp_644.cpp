#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums, long pos) {
    std::vector<long> result = nums;
    if (pos % 2 != 0) {
        std::reverse(result.begin(), result.end() - 1);
    } else {
        std::reverse(result.begin(), result.end());
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)1})), (3)) == (std::vector<long>({(long)6, (long)1})));
}
