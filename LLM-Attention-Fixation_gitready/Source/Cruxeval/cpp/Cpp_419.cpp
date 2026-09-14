#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    size_t found = text.find(value);
    if (found == std::string::npos) {
        return "";
    }
    return text.substr(0, found);
}
int main() {
    auto candidate = f;
    assert(candidate(("mmfbifen"), ("i")) == ("mmfb"));
}
