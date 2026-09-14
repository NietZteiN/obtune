#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    int pos = text.find(value);
    if (pos == 0) {
        return text.substr(value.length());
    } else {
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("coscifysu"), ("cos")) == ("cifysu"));
}
