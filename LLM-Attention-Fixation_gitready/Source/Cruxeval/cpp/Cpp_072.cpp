#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    for(char c : text) {
        if (!std::isdigit(c)) {
            return false;
        }
    }
    return !text.empty();
}
int main() {
    auto candidate = f;
    assert(candidate(("99")) == (true));
}
