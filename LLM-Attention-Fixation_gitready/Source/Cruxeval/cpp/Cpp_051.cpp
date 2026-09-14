#include<assert.h>
#include<bits/stdc++.h>
union Union_std_string_long{
    std::string f0;
    long f1;    Union_std_string_long(std::string _f0) : f0(_f0) {}
    Union_std_string_long(long _f1) : f1(_f1) {}
    ~Union_std_string_long() {}
    bool operator==(std::string f) {
        return f0 == f ;
    }    bool operator==(long f) {
        return f1 == f ;
    }
};
Union_std_string_long f(long num) {
    std::string s = std::string(10, '<');
    if (num % 2 == 0) {
        return Union_std_string_long(s);
    } else {
        return Union_std_string_long(num - 1);
    }
}
int main() {
    auto candidate = f;
    assert(candidate((21)) == 20);
}
