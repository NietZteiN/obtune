#include<assert.h>
#include<bits/stdc++.h>
long f(std::string full, std::string part) {
    size_t length = part.length();
    size_t index = full.find(part);
    int count = 0;
    while (index != std::string::npos) {
        full = full.substr(index + length);
        index = full.find(part);
        count++;
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("hrsiajiajieihruejfhbrisvlmmy"), ("hr")) == (2));
}
