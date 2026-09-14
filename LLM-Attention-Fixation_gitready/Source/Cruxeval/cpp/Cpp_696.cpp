#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int s = 0;
    for (int i = 1; i < text.length(); i++) {
        s += text.rfind(text[i]);
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("wdj")) == (3));
}
