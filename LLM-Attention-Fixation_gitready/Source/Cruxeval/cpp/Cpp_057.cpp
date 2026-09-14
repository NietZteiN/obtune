#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::transform(text.begin(), text.end(), text.begin(), ::toupper);
    int count_upper = 0;
    for (char& c : text) {
        if (std::isupper(c)) {
            count_upper++;
        } else {
            return 0;
        }
    }
    return count_upper / 2;
}
int main() {
    auto candidate = f;
    assert(candidate(("ax")) == (1));
}
