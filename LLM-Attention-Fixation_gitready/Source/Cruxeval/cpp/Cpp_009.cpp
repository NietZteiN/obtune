#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string t) {
    for (char c : t) {
        if (!std::isdigit(c)) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("#284376598")) == (false));
}
