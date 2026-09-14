#include <assert.h>
#include <bits/stdc++.h>
long f(std::string value, std::string character) {
    int total = 0;
    for (char c : value) {
        if (c == character[0] || c == std::tolower(character[0])) {
            total++;
        }
    }
    return total;
}
int main() {
    auto candidate = f;
    assert(candidate(("234rtccde"), ("e")) == (1));
}
