#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(long single_digit) {
    std::vector<long> result;
    for (int c = 1; c < 11; c++) {
        if (c != single_digit) {
            result.push_back(c);
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((5)) == (std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)6, (long)7, (long)8, (long)9, (long)10})));
}
