import type {
	ExpressiveCodeConfig,
	LicenseConfig,
	NavBarConfig,
	ProfileConfig,
	SiteConfig,
} from "./types/config";
import { LinkPreset } from "./types/config";

export const siteConfig: SiteConfig = {
	title: "茶猫小栈",
	subtitle: "一杯茶，一只猫，一整个世界。",
	lang: "zh_CN",
	themeColor: {
		hue: 35,
		fixed: false,
	},
	banner: {
		enable: true,
		src: "assets/images/demo-banner.png",
		position: "center",
		credit: {
			enable: false,
			text: "",
			url: "",
		},
	},
	toc: {
		enable: true,
		depth: 2,
	},
	favicon: [],
};

export const navBarConfig: NavBarConfig = {
	links: [
		LinkPreset.Home,
		LinkPreset.Archive,
		{
			name: "友链",
			url: "/links/",
		},
		{
			name: "留言",
			url: "/comment/",
		},
		LinkPreset.About,
	],
};

export const profileConfig: ProfileConfig = {
	avatar: "assets/images/demo-avatar.png",
	name: "茶猫",
	bio: "偶尔写写代码，偶尔画画图，偶尔发发呆。",
	links: [
		{
			name: "GitHub",
			icon: "fa6-brands:github",
			url: "https://github.com/neocat",
		},
	],
};

export const licenseConfig: LicenseConfig = {
	enable: true,
	name: "CC BY-NC-SA 4.0",
	url: "https://creativecommons.org/licenses/by-nc-sa/4.0/",
};

export const expressiveCodeConfig: ExpressiveCodeConfig = {
	theme: "github-dark",
};
