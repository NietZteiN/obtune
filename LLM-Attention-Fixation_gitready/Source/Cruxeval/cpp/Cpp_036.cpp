#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string chars) {
    return text.substr(0, text.find_last_not_of(chars) + 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("ha"), ("")) == ("ha"));
}
