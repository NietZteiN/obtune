#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string symbols) {
    int count = 0;
    if (!symbols.empty()) {
        for (char c : symbols) {
            count++;
        }
        text = std::string(text).append(text).append(text); // Equivalent to multiplying text by count
    }
    return text.insert(0, count*2, ' ').substr(2);
}
int main() {
    auto candidate = f;
    assert(candidate((""), ("BC1ty")) == ("        "));
}
