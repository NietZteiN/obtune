#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> digits) {
    std::reverse(digits.begin(), digits.end());
    if (digits.size() < 2) {
        return digits;
    }
    for (size_t i = 0; i < digits.size(); i += 2) {
        if (i + 1 < digits.size()) {
            std::swap(digits[i], digits[i + 1]);
        }
    }
    return digits;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2}))) == (std::vector<long>({(long)1, (long)2})));
}
