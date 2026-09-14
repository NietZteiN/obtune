#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string, long encryption) {
    if (encryption == 0) {
        return string;
    } else {
        std::string result = string;
        for (char& c : result) {
            if (isalpha(c)) {
                if (islower(c)) {
                    c = 'a' + (c - 'a' + encryption) % 26;
                } else {
                    c = 'A' + (c - 'A' + encryption) % 26;
                }
            }
        }
        return result;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("UppEr"), (0)) == ("UppEr"));
}
