#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result = "";
    int mid = (text.length() - 1) / 2;
    for (int i = 0; i < mid; i++) {
        result += text[i];
    }
    for (int i = mid; i < text.length() - 1; i++) {
        result += text[mid + text.length() - 1 - i];
    }
    return result.append(text.length() - result.length(), text.back());
}
int main() {
    auto candidate = f;
    assert(candidate(("eat!")) == ("e!t!"));
}
