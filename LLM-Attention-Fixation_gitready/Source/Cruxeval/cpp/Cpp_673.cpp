#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    if (std::all_of(string.begin(), string.end(), ::isupper)) {
        std::transform(string.begin(), string.end(), string.begin(), ::tolower);
    } else if (std::all_of(string.begin(), string.end(), ::islower)) {
        std::transform(string.begin(), string.end(), string.begin(), ::toupper);
    }
    return string;
}
int main() {
    auto candidate = f;
    assert(candidate(("cA")) == ("cA"));
}
