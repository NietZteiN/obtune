#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, long> f(std::string s) {
    long count = 0;
    std::string digits = "";
    for (char c : s) {
        if (isdigit(c)) {
            count += 1;
            digits += c;
        }
    }
    return std::make_tuple(digits, count);
}
int main() {
    auto candidate = f;
    assert(candidate(("qwfasgahh329kn12a23")) == (std::make_tuple("3291223", 7)));
}
