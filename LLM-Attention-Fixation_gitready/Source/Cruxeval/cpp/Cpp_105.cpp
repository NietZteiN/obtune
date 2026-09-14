#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for(int i = 0; i < text.size(); ++i)
    {
        if (i == 0 || !std::isalpha(text[i-1]))
        {
            if (std::islower(text[i]))
                text[i] = std::toupper(text[i]);
        }
        else
        {
            if (std::isupper(text[i]))
                text[i] = std::tolower(text[i]);
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("PermissioN is GRANTed")) == ("Permission Is Granted"));
}
