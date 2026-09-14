#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::stringstream ss(text);
    std::string line;
    int count = 0;
    while (std::getline(ss, line, '\n')) {
        count++;
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("145\n\n12fjkjg")) == (3));
}
