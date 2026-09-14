#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string num, long l) {
    std::string t = "";
    while (l > num.length()) {
        t += '0';
        l--;
    }
    return t + num;
}
int main() {
    auto candidate = f;
    assert(candidate(("1"), (3)) == ("001"));
}
