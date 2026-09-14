#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string a) {
    std::stringstream ss(a);
    std::string word, result;

    while (ss >> word) {
        result += word + " ";
    }

    result.pop_back(); // Remove the extra space at the end
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((" h e l l o   w o r l d! ")) == ("h e l l o w o r l d!"));
}
