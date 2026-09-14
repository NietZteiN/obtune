using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string book) {
        var a = book.Split(':');
        if (a[0].Split(' ').Last() == a[1].Split(' ').First())
            return F(string.Join(" ", a[0].Split().Reverse().Skip(1).Reverse()) + " " + a[1]);
        return book;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("udhv zcvi nhtnfyd :erwuyawa pun")).Equals(("udhv zcvi nhtnfyd :erwuyawa pun")));
    }

}
