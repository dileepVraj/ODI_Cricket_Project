interface FallbackBannerProps {
    message: string;
}

export default function FallbackBanner({ message }: FallbackBannerProps) {
    return <p className="badge badge-danger">{message}</p>;
}
