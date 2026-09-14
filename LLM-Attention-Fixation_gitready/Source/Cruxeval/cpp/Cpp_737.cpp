#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums) {
    long counts = 0;
    for (long i : nums) {
        if (std::to_string(i).find_first_not_of("0123456789") == std::string::npos) {
            if (counts == 0) {
                counts += 1;
            }
        }
    }
    return counts;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)6, (long)2, (long)-1, (long)-2}))) == (1));
}
