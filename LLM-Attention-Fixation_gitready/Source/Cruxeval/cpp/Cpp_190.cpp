#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string short_str = "";
    for (char c : text) {
        if (std::islower(c)) {
            short_str += c;
        }
    }
    return short_str;
}
int main() {
    auto candidate = f;
    assert(candidate(("980jio80jic kld094398IIl ")) == ("jiojickldl"));
}
