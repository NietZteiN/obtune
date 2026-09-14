#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int a = 0;
    if (text[0] != '\0' && text.find(text[0], 1) != std::string::npos) {
        a += 1;
    }
    for (size_t i = 0; i < text.length() - 1; i++) {
        if (text[i] != '\0' && text.find(text[i], i + 1) != std::string::npos) {
            a += 1;
        }
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("3eeeeeeoopppppppw14film3oee3")) == (18));
}
