#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    if (text.find_first_not_of(' ') == std::string::npos) {
        return text.size();
    }
    return 0;
}
int main() {
    auto candidate = f;
    assert(candidate((" 	 ")) == (0));
}
