#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long target) {
    long count = 0;
    for (long n1 : nums) {
        for (long n2 : nums) {
            count += (n1 + n2 == target);
        }
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3})), (4)) == (3));
}
