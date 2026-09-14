#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string txt) {
    std::string result = "";
    for (char c : txt) {
        if (isdigit(c)) {
            continue;
        }
        if (islower(c)) {
            result += toupper(c);
        } else if (isupper(c)) {
            result += tolower(c);
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("5ll6")) == ("LL"));
}
