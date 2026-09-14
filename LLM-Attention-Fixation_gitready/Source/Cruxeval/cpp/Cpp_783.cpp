#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string comparison) {
    int length = comparison.length();
    if (length <= text.length()) {
        for (int i = 0; i < length; i++) {
            if (comparison[length - i - 1] != text[text.length() - i - 1]) {
                return i;
            }
        }
    }
    return length;
}
int main() {
    auto candidate = f;
    assert(candidate(("managed"), ("")) == (0));
}
