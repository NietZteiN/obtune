#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text, std::string suffix) {
    if(suffix == "") {
        suffix = "";
    }
    return text.rfind(suffix) == (text.length() - suffix.length());
}
int main() {
    auto candidate = f;
    assert(candidate(("uMeGndkGh"), ("kG")) == (false));
}
